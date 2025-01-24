from flask import Flask, render_template, request, jsonify, flash, send_from_directory
from datetime import datetime, timedelta
import os

from db_api import *
from init_db import init_db

# Check if the database exists
if not os.path.exists('database/database.db'):
    print("Database does not exist. Initializing...")
    init_db()

# Create the Flask app
app = Flask(__name__, template_folder="templates")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():

    application_dates = get_application_date()
    date_list = []
    for row in application_dates:
        if row['application_date'] not in date_list:
            date_list.append(row['application_date'])

    company_names = get_company_names()

    # last 7 days
    date_list = sorted(date_list, key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
    latest_day = datetime.strptime(date_list[-1], "%Y-%m-%d") if date_list else datetime.now()
    dates = [(latest_day - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    last_7_days_application_numbers = []
    for date in dates:
        if date not in date_list:
            last_7_days_application_numbers.append(0)
        else:
            application = get_application(date)
            last_7_days_application_numbers.append(len(application))

    application_info = get_application_info()
    application_info_list = [dict(row) for row in application_info]
    info = {'application_numbers': len(application_info_list), 'offer_numbers': 0}
    for row in application_info_list:
        if row['interview_numbers'] not in info.keys():
            info[row['interview_numbers']] = 1
        else:
            info[row['interview_numbers']] += 1
        if row['offer'] == 1:
            info['offer_numbers'] += 1

    stages = [{"stage": "Applications", "count": info['application_numbers']}]

    max_round = max((k for k in info.keys() if isinstance(k, int)), default=0)  # 找到最大面试轮次
    for i in range(1, max_round + 1):
        stages.append({"stage": f"{i} Interview", "count": info.get(i, 0)})
    stages.append({"stage": "Offers", "count": info['offer_numbers']})

    return render_template('index.html', date_list=date_list, company_list=company_names, dates=dates, counts=last_7_days_application_numbers, stages=stages)


# Fetch the application data
@app.route('/fetch_applications', methods=['GET', 'POST'])
def fetch_application():
    date = request.args.get('date')

    results = get_application(date)
    applications = [dict(result) for result in results]

    return jsonify({'applications': applications})


# Fetch titles
@app.route('/fetch_titles', methods=['GET', 'POST'])
def fetch_titles():
    company_name = request.args.get('company')
    results = get_title_names(company_name)
    titles = [dict(result) for result in results]
    return jsonify({'titles': titles})


# Search for the application
@app.route('/search_applications', methods=['GET', 'POST'])
def search_applications():
    search_text = request.get_json()
    company_name = search_text['company']
    title_name = search_text['title']
    results = search_application(company_name, title_name)
    applications = [dict(result) for result in results]

    return jsonify({'applications': applications})


# 更新应用数据的路由
@app.route('/update_application', methods=['POST'])
def update_application():
    data = request.get_json()
    application_id = data['id']
    value = data['value']

    # Get the update response
    response = update_interview_offer(application_id, value)
    response_data = response.get_json()

    if not response_data["success"]:
        flash(response_data["error"], "error")
        return response

    try:
        # Get updated application info
        application_info = get_application_info()
        application_info_list = [dict(row) for row in application_info]

        # Calculate new stages distribution
        info = {'application_numbers': len(application_info_list), 'offer_numbers': 0}
        for row in application_info_list:
            if row['interview_numbers'] not in info.keys():
                info[row['interview_numbers']] = 1
            else:
                info[row['interview_numbers']] += 1
            if row['offer'] == 1:
                info['offer_numbers'] += 1

        max_round = max(k for k in info.keys() if isinstance(k, int))
        for i in range(max_round, 0, -1):
            if i < max_round:
                if i not in info.keys():
                    info[i] = info.get(i + 1, 0)
                    continue
                info[i] += info[i + 1]

        # Format stages data
        stages = [{"stage": "Applications", "count": info['application_numbers']}]
        # max_round = max(k for k in info.keys() if isinstance(k, int))
        for i in range(1, max_round + 1):
            stages.append({"stage": f"{i} Interview", "count": info.get(i, 0)})
        stages.append({"stage": "Offers", "count": info['offer_numbers']})

        # Include stages in the response
        response_data['stages'] = stages
        return jsonify(response_data)

    except Exception as e:
        print(f"Error calculating stages data: {str(e)}")
        return response


@app.route('/delete_application', methods=['POST'])
def delete_application():
    data = request.json
    application_id = data.get('id')

    if not application_id:
        return jsonify({'success': False, 'message': 'Invalid application ID'}), 400

    response = delete_job_application(application_id)

    return response


@app.route('/add_application', methods=['POST'])
def add_application():
    try:
        data = request.json

        # Validate required fields
        required_fields = ['company_name', 'title_name', 'application_date']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400


        success, message, new_id = insert_application(data)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'application_id': new_id
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/update_stage', methods=['POST'])
def update_stage():
    data = request.get_json()
    application_id = data.get('application_id')
    delta = data.get('delta')

    # Get the stage update results
    results = update_interview_stage(application_id, delta)

    # If the update was successful, get the updated stages data
    if results.get('success'):
        try:
            # Reuse the existing function to get application info
            application_info = get_application_info()
            application_info_list = [dict(row) for row in application_info]

            # Calculate the stages distribution
            info = {'application_numbers': len(application_info_list), 'offer_numbers': 0}
            for row in application_info_list:
                if row['interview_numbers'] not in info.keys():
                    info[row['interview_numbers']] = 1
                else:
                    info[row['interview_numbers']] += 1
                if row['offer'] == 1:
                    info['offer_numbers'] += 1

            max_round = max(k for k in info.keys() if isinstance(k, int))
            for i in range(max_round, 0, -1):
                if i < max_round:
                    if i not in info.keys():
                        info[i] = info.get(i + 1, 0)
                        continue
                    info[i] += info[i + 1]



            # Format stages data
            stages = [{"stage": "Applications", "count": info['application_numbers']}]
            # max_round = max(k for k in info.keys() if isinstance(k, int))
            for i in range(1, max_round + 1):
                stages.append({"stage": f"{i} Interview", "count": info.get(i, 0)})
            stages.append({"stage": "Offers", "count": info['offer_numbers']})

            # Include stages data in the response
            results['stages'] = stages

        except Exception as e:
            print(f"Error calculating stages data: {str(e)}")
            # Still return success for the stage update, even if getting stages distribution failed
            return jsonify(results)

    return jsonify(results)


if __name__ == '__main__':

    app.run(debug=True)

