// window.stages = JSON.parse(document.getElementById('stages-data').textContent);
// console.log(window.stages);

let weeklyTrendChart = null;  // 存储图表实例
let funnelChart = null;       // 存储图表实例
let currentDeleteId = null;   // 当前待删除的申请ID

function toggleGroup(date) {
    const group = document.getElementById(`group-${date}`);
    const arrow = document.querySelector(`.date-group-header[data-date="${date}"] .arrow`);
    if (group.style.display === 'none' || group.style.display === '') {
        fetchApplications(date);
        group.style.display = 'table';
        arrow.innerHTML = '&#9660;';
    } else {
        group.style.display = 'none';
        arrow.innerHTML = '&#9654;';
        clearTableContent(date);
    }
}

function clearTableContent(date) {
    document.getElementById(`table-body-${date}`).innerHTML = '';
    document.getElementById(`table-body-search-results-${date}`).innerHTML = '';
}

function fetchApplications(date) {
    fetch(`/fetch_applications?date=${date}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById(`table-body-${date}`);
            tableBody.innerHTML = '';

            data.applications.forEach(application => {
                const row = `
                    <tr class="${application.offer ? 'gold-background' : ''}">
                        <td>${application.application_id}</td>
                        <td>${application.application_date}</td>
                        <td>${application.company_name}</td>
                        <td>${application.title_name}</td>
                        <td>
                            <div class="stage-controls">
                                <span class="stage-number">${application.interview_numbers}</span>
                                <div class="stage-arrows">
                                    <span class="stage-arrow" onclick="updateStage(${application.application_id}, 1, this.closest('.stage-controls').querySelector('.stage-number'))">▲</span>
                                    <span class="stage-arrow" onclick="updateStage(${application.application_id}, -1, this.closest('.stage-controls').querySelector('.stage-number'))">▼</span>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="action-cell">
                                <input type="checkbox"
                                       data-id="${application.application_id}"
                                       data-field="offer"
                                       ${application.offer ? 'checked' : ''}>
                                <span class="delete-btn" onclick="showDeleteModal(${application.application_id})">×</span>
                            </div>
                        </td>
                    </tr>
                `;
                tableBody.insertAdjacentHTML('beforeend', row);
            });

            attachCheckboxListeners();
        })
        .catch(error => {
            console.error('Error fetching applications:', error);
            alert('Failed to fetch applications. Please try again.');
        });
}

function attachCheckboxListeners() {
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const applicationId = this.getAttribute('data-id');
            const value = this.checked ? 1 : 0;

            fetch('/update_application', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: applicationId,
                    value: value
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const row = this.closest('tr');
                        if (this.checked) {
                            row.classList.add('gold-background');
                        } else {
                            row.classList.remove('gold-background');
                        }

                        // Update funnel chart if stages data is provided in the response
                        if (data.stages) {
                            initFunnelChart(data.stages);
                        }
                    } else {
                        alert('Update failed. Please try again.');
                        this.checked = !this.checked;
                    }
                })
                .catch(error => {
                    console.error('Error updating application:', error);
                    alert('Failed to update application. Please try again.');
                    this.checked = !this.checked;
                });
        });
    });
}

function fetchTitles() {
    const company = document.getElementById('company-select').value;
    if (company) {
        fetch(`/fetch_titles?company=${company}`)
            .then(response => response.json())
            .then(data => {
                const titleSelect = document.getElementById('title-select');
                titleSelect.innerHTML = '<option value="">Select a title</option>';

                data.titles.forEach(title => {
                    const option = `<option value="${title.title_name}">${title.title_name}</option>`;
                    titleSelect.insertAdjacentHTML('beforeend', option);
                });
            })
            .catch(error => {
                console.error('Error fetching titles:', error);
                alert('Failed to fetch titles. Please try again.');
            });
    }
}

function searchApplications() {
    const company = document.getElementById('company-select').value;
    const title = document.getElementById('title-select').value;

    if (company && title) {
        fetch('/search_applications', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company: company,
                title: title
            })
        })
            .then(response => response.json())
            .then(data => {
                // 清除所有现有的搜索结果
                document.querySelectorAll('.applications-table').forEach(table => {
                    table.style.display = 'none';
                });
                document.querySelectorAll('.date-group-header .arrow').forEach(arrow => {
                    arrow.innerHTML = '&#9654;';
                });

                const applicationsByDate = {};
                data.applications.forEach(application => {
                    const date = application.application_date;
                    if (!applicationsByDate[date]) {
                        applicationsByDate[date] = [];
                    }
                    applicationsByDate[date].push(application);
                });

                for (const date in applicationsByDate) {
                    const applications = applicationsByDate[date];
                    const tableBody = document.getElementById(`table-body-search-results-${date}`);
                    tableBody.innerHTML = '';

                    applications.forEach(application => {
                        const row = `
                            <tr class="${application.offer ? 'gold-background' : ''}">
                                <td>${application.application_id}</td>
                                <td>${application.application_date}</td>
                                <td>${application.company_name}</td>
                                <td>${application.title_name}</td>
                                <td>
                                    <div class="stage-controls">
                                        <span>${application.interview_numbers}</span>
                                        <div class="stage-arrows">
                                            <span class="stage-arrow" onclick="updateStage(${application.application_id}, 1, this)">▲</span>
                                            <span class="stage-arrow" onclick="updateStage(${application.application_id}, -1, this)">▼</span>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="action-cell">
                                        <input type="checkbox"
                                               data-id="${application.application_id}"
                                               data-field="offer"
                                               ${application.offer ? 'checked' : ''}>
                                        <span class="delete-btn" onclick="showDeleteModal(${application.application_id})">×</span>
                                    </div>
                                </td>
                            </tr>
                        `;
                        tableBody.insertAdjacentHTML('beforeend', row);
                    });

                    const group = document.getElementById(`group-${date}`);
                    group.style.display = 'table';
                    document.querySelector(`.date-group-header[data-date="${date}"] .arrow`).innerHTML = '&#9660;';
                }

                attachCheckboxListeners();
            })
            .catch(error => {
                console.error('Error searching applications:', error);
                alert('Failed to search applications. Please try again.');
            });
    }
}

function initWeeklyTrendChart() {
    const ctx = document.getElementById('weeklyTrendChart').getContext('2d');
    if (weeklyTrendChart instanceof Chart) {
        weeklyTrendChart.destroy();
    }

    const dates = JSON.parse(document.getElementById('dates-data').textContent);
    const applicationCounts = JSON.parse(document.getElementById('counts-data').textContent);

    weeklyTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Applications',
                data: applicationCounts,
                borderColor: '#4F46E5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#FFF',
                pointBorderColor: '#4F46E5',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                tooltip: {
                    backgroundColor: '#FFF',
                    titleColor: '#111827',
                    bodyColor: '#111827',
                    borderColor: '#E5E7EB',
                    borderWidth: 1,
                    padding: 10,
                    boxWidth: 10,
                    boxHeight: 10,
                    cornerRadius: 4,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#E5E7EB'
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function initFunnelChart(stages = null) {
    const ctx = document.getElementById('funnelChart').getContext('2d');

    // Destroy existing chart if it exists
    if (funnelChart) {
        funnelChart.destroy();
    }
    const stagesData = document.getElementById('stages-data').textContent;
    const tempstages = JSON.parse(stagesData);

    // If no stages provided, use the ones from the template
    const chartData = tempstages || window.stages|| [];
    const data = chartData.filter(item => item.count > 0);

    funnelChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.stage),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [
                    '#4F46E5',
                    '#7C3AED',
                    '#9333EA',
                    '#C026D3',
                    '#DB2777'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#FFF',
                    titleColor: '#111827',
                    bodyColor: '#111827',
                    borderColor: '#E5E7EB',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: '#E5E7EB'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    return funnelChart;
}

function updateStage(applicationId, delta, stageElement) {
    if (!stageElement) {
        console.error('Stage element not found');
        return;
    }

    fetch('/update_stage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            application_id: applicationId,
            delta: delta
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data && data.success === true && 'new_stage' in data) {
                // Update the stage number in the UI
                stageElement.textContent = data.new_stage;

                // If the response includes updated stages data, use it to update the chart
                if (data.stages) {
                    initFunnelChart(data.stages);
                } else {
                    // Reload the page as fallback if no stages data provided
                    window.location.reload();
                }
            } else {
                console.error('Invalid response data:', data);
                alert('Failed to update stage. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error updating stage:', error);
            alert('Failed to update stage. Please try again.');
        });
}

function showDeleteModal(applicationId) {
    currentDeleteId = applicationId;
    document.getElementById('deleteModal').style.display = 'block';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    currentDeleteId = null;
}

function confirmDelete() {
    if (currentDeleteId === null) return;

    fetch('/delete_application', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: currentDeleteId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 删除成功后直接刷新整个页面
                window.location.reload();
            } else {
                alert('Failed to delete application. Please try again.');
                closeDeleteModal();
            }
        })
        .catch(error => {
            console.error('Error deleting application:', error);
            alert('Failed to delete application. Please try again.');
            closeDeleteModal();
        });
}

function showAddModal() {
    const modal = document.getElementById('addModal');
    console.log(modal)
    modal.style.display = 'block';

    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('add-date').value = today;
}

function closeAddModal() {
    const modal = document.getElementById('addModal');
    modal.style.display = 'none';
    // Clear form
    document.getElementById('add-company').value = '';
    document.getElementById('add-title').value = '';
}

function confirmAdd() {
    const company = document.getElementById('add-company').value.trim();
    const title = document.getElementById('add-title').value.trim();
    const date = document.getElementById('add-date').value;

    if (!company || !title || !date) {
        alert('Please fill in all required fields.');
        return;
    }

    fetch('/add_application', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            company_name: company,
            title_name: title,
            application_date: date,
            offer: 0               // Default value
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();  // Refresh page to show new data
            } else {
                alert('Failed to add application. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error adding application:', error);
            alert('Failed to add application. Please try again.');
        });
}

// Initialize charts when the page loads
window.addEventListener('load', () => {
    initWeeklyTrendChart();
    initFunnelChart();
    // closeDeleteModal();
    // closeAddModal();
});

// Update charts when window is resized
window.addEventListener('resize', () => {
    if (weeklyTrendChart) {
        weeklyTrendChart.resize();
    }
    if (funnelChart) {
        funnelChart.resize();
    }
});

// Close modal when clicking outside
window.onclick = function (event) {
    if (event.target === document.getElementById('deleteModal')) {
        closeDeleteModal();
    }
    if (event.target === document.getElementById('addModal')) {
        closeAddModal();
    }
}