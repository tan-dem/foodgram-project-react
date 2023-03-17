# Foodgram

Web-service where users can post recipes, subscribe to other users' posts, add recipes to favorites, add recipes to shopping cart and download the shopping list including all the necessary ingredients.  

**Technologies:** Python 3.7, Django Rest Framework  
**Author:** [@tan-dem](https://github.com/tan-dem)

Examples of requests to API and responses:  

* Registration of new user, POST: `/api/users/`  

```
{  
  "email": "vpupkin@yandex.ru",  
  "username": "vasya.pupkin",  
  "first_name": "Вася",  
  "last_name": "Пупкин",  
  "password": "Qwerty123"  
} 
```

Response:  
```
{  
  "email": "vpupkin@yandex.ru",  
  "id": 0,  
  "username": "vasya.pupkin",  
  "first_name": "Вася",  
  "last_name": "Пупкин"  
} 
```

* Getting the list of all recipes, GET: `/api/recipes/`  

Response:  
```
{  
  "count": 123,  
  "next": "http://foodgram.example.org/api/recipes/?page=4",  
  "previous": "http://foodgram.example.org/api/recipes/?page=2",  
  "results": [  
    {  
      "id": 0,  
      "tags": [  
        {  
          "id": 0,  
          "name": "Завтрак",  
          "color": "#E26C2D",  
          "slug": "breakfast"  
        }  
      ],  
      "author": {  
        "email": "user@example.com",  
        "id": 0,  
        "username": "string",  
        "first_name": "Вася",  
        "last_name": "Пупкин",  
        "is_subscribed": false  
      },  
      "ingredients": [  
        {  
          "id": 0,  
          "name": "Картофель отварной",  
          "measurement_unit": "г",  
          "amount": 1  
        }  
      ],  
      "is_favorited": true,  
      "is_in_shopping_cart": true,  
      "name": "string",  
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",  
      "text": "string",  
      "cooking_time": 1  
    }  
  ]  
}
``` 

* Subscription to the user, POST: `/api/users/{id}/subscribe/`  

Response:  
```
{  
  "email": "user@example.com",  
  "id": 0,  
  "username": "string",  
  "first_name": "Вася",  
  "last_name": "Пупкин",  
  "is_subscribed": true,  
  "recipes": [  
    {  
      "id": 0,  
      "name": "string",  
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",  
      "cooking_time": 1  
    }  
  ],  
  "recipes_count": 0  
}
``` 

Full information with the list of the available endpoints is accessible via `/redoc/`
