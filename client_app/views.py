import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages

# Base URL of the backend API
API_BASE_URL = 'http://127.0.0.1:8000/api'

def index(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'student')  # default to student

        payload = {
            'username': username,
            'password': password,
            'role': role
        }
        url = f"{API_BASE_URL}/users/register/"
        response = requests.post(url, data=payload)
        if response.status_code == 201:
            messages.success(request, "Registration successful!")
            return redirect('login')
        else:
            messages.error(request, "Registration failed: " + str(response.json()))
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        url = f"{API_BASE_URL}/users/login/"
        response = requests.post(url, data={'username': username, 'password': password})
        if response.status_code == 200:
            data = response.json()
            # Store tokens in session
            request.session['access'] = data['access']
            request.session['refresh'] = data['refresh']
            request.session['role'] = data['role']
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('home')

def exam_list_view(request):
    """
    GET list of exams from backend, show to user
    """
    access = request.session.get('access')
    if not access:
        messages.error(request, "Please login first.")
        return redirect('login')

    url = f"{API_BASE_URL}/exams/list/"
    headers = {'Authorization': f'Bearer {access}'}
    response = requests.get(url, headers=headers)
    exam_list = []
    if response.status_code == 200:
        exam_list = response.json()
    return render(request, 'exam.html', {'exams': exam_list})

def take_exam_view(request, exam_id):
    """
    Show the questions in an exam to the student.
    """
    access = request.session.get('access')
    if not access:
        messages.error(request, "Please login first.")
        return redirect('login')

    # 1) fetch exam detail
    exam_url = f"{API_BASE_URL}/exams/list/"
    headers = {'Authorization': f'Bearer {access}'}
    response = requests.get(exam_url, headers=headers)
    if response.status_code == 200:
        all_exams = response.json()
        # find the exam of interest
        exam_data = next((e for e in all_exams if e['id'] == exam_id), None)
        if not exam_data:
            messages.error(request, "Exam not found.")
            return redirect('exam_list')

        if request.method == 'POST':
            # 2) collect answers
            answers = []
            for question in exam_data['questions']:
                q_id = question['id']
                chosen_option = request.POST.get(f'question_{q_id}', None)
                if chosen_option is not None:
                    answers.append({'question_id': q_id, 'option_id': int(chosen_option)})
                else:
                    answers.append({'question_id': q_id, 'option_id': None})

            submit_url = f"{API_BASE_URL}/exams/submit/"
            payload = {
                'exam_id': exam_data['id'],
                'answers': answers
            }
            submit_resp = requests.post(submit_url, headers=headers, json=payload)
            if submit_resp.status_code == 200:
                result_data = submit_resp.json()
                messages.success(request, "Exam submitted! Score: {} / {}, Passed: {}".format(
                    result_data['score'], result_data['total'], result_data['passed']
                ))
                return redirect('exam_results')
            else:
                messages.error(request, "Error submitting exam.")
        return render(request, 'take_exam.html', {'exam': exam_data})
    else:
        messages.error(request, "Unable to fetch exam.")
        return redirect('exam_list')

def exam_results_view(request):
    """
    Show the results of the user or all results if admin
    """
    access = request.session.get('access')
    if not access:
        messages.error(request, "Please login first.")
        return redirect('login')

    url = f"{API_BASE_URL}/exams/results/"
    headers = {'Authorization': f'Bearer {access}'}
    response = requests.get(url, headers=headers)
    results = []
    if response.status_code == 200:
        results = response.json()
    return render(request, 'result.html', {'results': results})
