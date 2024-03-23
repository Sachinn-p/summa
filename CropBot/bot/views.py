# views.py

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse, Body, Message, Redirect 
from .query_weather import get_weather, generate_weather_params, model_predict
from django.conf import settings

@csrf_exempt
def webhook(request):
    response = MessagingResponse()

    if request.method == "POST":
        # Get location and soil parameters from the form
        location = request.POST.get('location')
        soil_params = request.POST.get('soil_params')

        if location and soil_params:
            lat, lon = map(float, location.split(','))  # Splitting latitude and longitude
            weather_response = get_weather(lat, lon, 'd0a2301b1066be60a90b946462380bab')
            weather_params = generate_weather_params(weather_response)
            request.session['temp'] = weather_params["temperature"]
            request.session['humid'] = weather_params["humidity"]
            message_body1 = f"*Great! We got your co-ordinates.*\n\n"\
                            f"{weather_params['location']}, {weather_params['description']}\n"\
                            f"Temperature: {weather_params['temperature']}\n"\
                            f"Humidity: {weather_params['humidity']}\n"
            
            message_body2 = f"Now please tell us about your *Soil Quality* in the following format:\n\n"\
                            f"1. Nitrogen Content (in mg/kg).\n"\
                            f"2. Phosphorus Content (in mg/kg).\n"\
                            f"3. Potassium Content (in mg/kg).\n"\
                            f"4. pH of the Soil (in the range of 1 to 14).\n"\
                            f"5. Annual Rainfall (in mm).\n"

            response.message(message_body1)
            response.message(message_body2)
            
        elif soil_params:
            params = [float(param.strip()) for param in soil_params.split('\n')]
            message_body = model_predict(params[0], params[1], params[2], request.session['temp'], request.session['humid'], params[3], params[4], request)
            response.message(message_body)
        else:
            response.message("Please provide your location and soil parameters.")

    return HttpResponse(response.to_xml(), content_type='text/xml')
