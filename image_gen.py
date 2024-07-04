import requests
import base64
import os
url = "http://127.0.0.1:7860"
def image_generator(prompt = "Sunset in the mountains, lake in front",neg_prompt = "",count = 0):
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

    data = {
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "sampler_name": "Euler",
        "steps": 20,
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "seed": -1
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        response_data = response.json()
        images = response_data.get('images', [])

        if not os.path.exists('output_images'):
            os.makedirs('output_images')

        for i, img_data in enumerate(images):
            img_data = base64.b64decode(img_data)
            with open(f'output_images/image_{count}.png', 'wb') as img_file:
                img_file.write(img_data)
        
        print("Images saved successfully!")
    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)

#def get_models():
#    
#    opt = requests.get(url=f'{url}/sdapi/v1/options')
#    opt_json = opt.json()
#    opt_json['sd_model_checkpoint'] = '<MODEL_NAME>'
#    requests.post(url=f'{url}/sdapi/v1/options', json=opt_json)
#    payload ={}
#    response = requests.get(url=f'{url}/sdapi/v1/sd-models', json=payload)
#    print(response.json())