import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
import logging

logger = logging.getLogger(__name__)

@xframe_options_exempt
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def ask(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')
            logger.debug(f'Received question: {question}')

            # Send the request to ollama API
            response = requests.post(
                'https://gsz-sandbox.emea.sas.com/ollama/api/generate',
                headers={
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama2',
                    'prompt': question,
                    'stream': False  # o True, a seconda delle tue esigenze
                },
                verify=False  # Ignore SSL certificate verification
            )

            logger.debug(f'API response status: {response.status_code}')
            logger.debug(f'API response content: {response.content}')

            if response.status_code == 200:
                response_json = response.json()
                answer = response_json.get('response', 'No answer returned')
                logger.debug(f'Answer: {answer}')
                return JsonResponse({'answer': answer})
            else:
                logger.error(f'Failed to get a response from the API, status code: {response.status_code}')
                return JsonResponse({'error': 'Failed to get a response from the API'}, status=response.status_code)

        except json.JSONDecodeError as e:
            logger.error(f'JSON decode error: {str(e)}')
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except requests.RequestException as e:
            logger.error(f'Request exception: {str(e)}')
            return JsonResponse({'error': 'Request to API failed'}, status=500)
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
