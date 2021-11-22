"""View module for handling requests about events"""
from django.core.exceptions import ValidationError
from rest_framework import status
#from django.http import HttpResponseServerError  NOT BEING USED YET
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from levelupapi.models import Event, Game, Gamer  
from django.contrib.auth.models import User  # remember- user is from django, it's not a model we made specifically for this program 
from rest_framework.decorators import action


class EventView(ViewSet): #holds the functions to create, list, etc

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ CREATE METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def create(self, request): #The create method holds 2 parameters: self and request
                               # If you look at the event model, you'll see we need to grab foreign keys from several objects to create a new event 
                               # We need to grab the logged in gamer to make an organizer, a game to make a game, 
        """Handle POST operations
        Returns: Response -- JSON serialized event instance
        """
        organizer = Gamer.objects.get(user=request.auth.user)#We need to grab the logged in user and store them as this event's organizer.
                                                             #Gamer is gamer model.  objects.get is an ORM.  .get is the ORM for grabbing a single item
                                                             #It will let us grab the user via their auth token.  
                                                             #Since we're using the gamer model, we have to import Gamer from levelupapi.models

         #vvvvvv part in bracket should be however its named in front end; when testing in postman use front end formatting for property names but use backend model to know what properties to include
        game = Game.objects.get(pk=request.data['gameId'])     # Next we need to grab the game object for the correct game (monopoly, etc).
                                                                # We use an ORM method on the Game model to grab the correct game object 
                                                                # For example, if it's a Risk event, grab the game object for Risk
                                                                # We do that by making pk equal to request.data, 
                                                                # That's because the field on request that gives us the body coming in from postman is the data field.
                                                                # Since data will be a dictionary type of state, we access the game id out of it with bracket notation
                                                                #We also need to make sure we import Game from levelupapi at the top of this file
        #Next we need a try and except section 
        #This section is where we try to create a new event object in our database.
        #Event.objects has a ORM used on it called .create that adds a new obj to the Events database
        #Inside create's parentheses, we put in all the fields we want in the object we're creating
        #It should match up to the properties in the Event model
        try:
            event = Event.objects.create(
                game=game,                  #game will be set to the variable we made above to grab the correct game
                organizer=organizer,        #organizer will be set to the variable we made above to grab the user creating the event  
                description=request.data['description'], #description will be pulled from the request data's (that's in dictionary form) description property
                date=request.data['date'], #date will be pulled from the request data's (that's in dictionary form) date property
                time=request.data['time'] #time will be pulled from the request data's (that's in dictionary form) time property
            ) 
            #Next we call the event serializer so we can return the created object to the front end
            #REMEMBER serializer turns it into JSON format so it can be sent to front end
            event_serializer = EventSerializer(event, context={'request': request}) #make a variable to hold invoking EventSerializer
                                                                                    #Note: code that does serializer logic is further down in this file
                                                                                    #Pass in 2 args- the object we tried to build, and needed info for the header
            return Response(event_serializer.data, status=status.HTTP_201_CREATED)  # The big return is the event and header info that's been serialized and the status code to confirm it was created
        except ValidationError as ex:   #catch any errors that occur diring the try process 
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST) #The dictionary will have a 'message' key/property, and it's value will be ??????? and a 400 status message


    def create(self, request):
       
         organizer = Gamer.objects.get(user=request.auth.user)
         game = Game.objects.get(pk=request.data['gameId'])
         
         try:
            event = Event.objects.create(
                game=game,                  
                organizer=organizer,        
                description=request.data['description'], 
                date=request.data['date'], 
                time=request.data['time'] 
            ) 
            
            event_serializer = EventSerializer(event)
            return Response(event_serializer.data, status=status.HTTP_201_CREATED)
         
         except ValidationError as ex:   
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ LIST METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def list(self, request):
        """Handle GET requests to events resource

        Returns:
            Response -- JSON serialized list of events
        """
        # Get the current authenticated user
        gamer = Gamer.objects.get(user=request.auth.user)
        events = Event.objects.all()

        # Set the `joined` property on every event
        for event in events:
            # Check to see if the gamer is in the attendees list on the event
            event.joined = gamer in event.attendees.all()

        # Support filtering events by game
        game = self.request.query_params.get('gameId', None)
        if game is not None:
            events = events.filter(game__id=type)

        serializer = EventSerializer(
            events, many=True, context={'request': request})
        return Response(serializer.data)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ RETRIEVE METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
    #The retrieve method is a lot like list, except retrieve will GET a single event. 

    def retrieve(self, request, pk):             # The retrieve method takes an extra argument - pk - because 
                                                # you are getting a single specific event

        event = Event.objects.get(pk=pk)         # Make a new variable called event.  Use the ORM .get method 
                                                # and pass the pk of the event you want into it.

        event_serializer = EventSerializer(event, context={'request': request}) # Make a new variable 'event_serializer'.  
                                                                                # In it, call the EventSerializer and pass in the event 
                                                                                # variable you just made and the context info for the headers

        return Response(event_serializer.data)   #return will be the result of the EventSerializer call inside event_serializer variable




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ DESTROY METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
    # The destroy method looks similar to the retrieve method, except we're deleting a single event instead of 
    # getting and returning it.  That means we won't involve any serializers.

    def destroy(self, request, pk):             # The retrieve method takes an extra argument - pk - because 
                                                # you are getting a single specific event

        event = Event.objects.get(pk=pk)         # Make a new variable called event.  Use the ORM .get method 
                                                # and pass the pk of the event you want into it.

        event.delete()        #Call the delete() ORM on the event variable you just made
 
        return Response(None, status=status.HTTP_204_NO_CONTENT)   # Return will be the result of the .delete().  
                                 # 'None' refers to the data included in the return.  
                                 # status is the HTTP code that signals a successful deletion- '204 no content'





#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ UPDATE METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
    #The update method is a lot the retreive method because we are dealing with a single event

    def update(self, request, pk):             # The update method takes an extra argument - pk - because 
                                               # you are updating a single specific event

        event = Event.objects.get(pk=pk)        # Make a new variable called event.  Use the ORM .get method 
                                                # and pass the pk of the event you want into it.

        event.date = request.data['date']       # Now that we grabbed the correct event, we do our updates.
                                                # Here, we're updating the event's date.
                                                # We get the updated value for 'date' from the request.  
                                                # The request is in the data form of a dictionary so we need 
                                                # bracket notation to get to the 'date' key:value.
                                            
        event.time = request.time['time']                       # Here we're updating the time
        event.description = request.description['description']  # Here we're updating the description

        event.game = Game.objects.get(pk=request.data['gameId'])   # Here we're updating the game.  This one is trickier.
                                                                   # We have to grab the game object or we'll get an error
                                                                   # use the .get ORM on the Game model and pass the gameId from 
                                                                   # the update request into the ORM as the pk
        
        event.save()   # After we've done the changes above, we call the save method on the event

        return Response(None, status=status.HTTP_204_NO_CONTENT)   # Return will be the result of the .save().  
                                 # 'None' refers to the data included in the return.  
                                 # status is the HTTP code that signals a successful update- '204 no content'


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ CUSTOM ACTION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Now we add a custom action.  That means we want the user to be able to make a more specific request that causes an specific response.  
# The custom action is: the user can sign up or cancel their attendance in an event using this url:

# http://localhost:8000/events/2/signup
# where 2 is will be the event's pk; signup is the custom event's name.  Whatever we name it, that's what will appear here in the url 

# to build a custom event, you need a 'decorator'.  Then you set up what the event will do
# this event will act differently based on a client-side request for post or delete

    @action(methods=['post', 'delete'], detail=True)        # @action is a 'decorator' that turns this method into a resource that we can hit on the front end. 
                                                            # We have to import @action at the top of the file. 
                                                            # We specify which methods it will take [post and delete] 
                                                            # The other attribute we pass in is detail. We set it equal to True.  This is what gives us the pk of the event inside the url.
    
    def signup(self, request, pk):                          # this is the custom action.  We named it signup. 
                                                            # It has 2 parameters- self, the request, and pk (we need pk since detail=True on the decorator)
        
        gamer = Gamer.objects.get(user=request.auth.user)   # We grab the gamer that's logged in.  We use the .get ORM  on the Gamer model 
                                                            # and get the object where the user equals the logged in user (user=request.auth.user)
        
        event =  Event.objects.get(pk=pk)                   # We grab the correct event by the event pk

        # The code to grab the gamer and event will happen whether our custom action is a post or delete request.  Then, there are if statements:
        
        if request.method == 'POST':                                #If the request is POST aka a user is signing up for an event
            
            event.attendees.add(gamer)                              # add is a function on the many to many field that adds an object to that list.  
                                                                    # Here, we're adding the gamer object we grabbed up above and adding it to the attendees objects.  
                                                                    # attendees is a many to many field on event.  
            
            return Response({}, status=status.HTTP_201_CREATED)      # we don't really need to return much because the front end will rerender the event list when the button is clicked.  
                                                                     # Just an empty object and status code.
        
        if request.method == "DELETE":
            event.attendees.remove(gamer)                                #.remove is a function on the many to many field to remove the gamer object
            return Response({}, status=status.HTTP_204_NO_CONTENT)      #response is an empty dictionary and status code

        #The next step is to go to the front end code.  
        # In eventmanager.js we'll need a joinEvent function that fetches the url from our custom event and has a POST method.
        # In eventlist.js, we need a 'join this event' button for users to click.



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ SERIALIZERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#Now we define our needed serializers.  This section is tricky because we have to limit what information about the organizer aka user 
#is passed back to the front end.  We only want to pass the first and last name, not stuff like the user's password. To limit what gets passed 
#back, we build several serializers and call them inside of each other, AKA we make nested serializers.  
#The EventSerializer would pass back too much user info in the 'organizer' field, so we make a GamerSerializer that lets us serialize
#the user, then the UserSerializer lets us limit what gets serialized from the user field.
#Honestly it's a big rabbit hole of cause and effect
#Since the serializer code bounces around I numbered the steps in the order pieces are built


class UserSerializer(serializers.ModelSerializer):                # STEP_7: Define the new serializer Userserializer.  It's also a model serializer
    class Meta:
        model = User 
        fields = ('first_name', 'last_name')                      # STEP_8: Pull out just the first and last name.  Also, you'll need to import the user. You 
                                                                          #can go to models>gamer.py and copy the user import from the top
                                                                          #of it, then past it at the top of this file.  looks like 'from django.contrib.auth.models import User'


class GamerSerializer(serializers.ModelSerializer):              # STEP_4: Define the new serializer GamerSerializer.  It's also a model serializer
    
    user = UserSerializer()                                      # STEP_6: Make a new variable called user and call a new serializer called UserSerializer

    class Meta: 
        model = Gamer
        fields = ['user']                                        # STEP_5: at this point it would only pass the user id. We could  
        depth = 1                                                          #try to get more user info by doing 'depth = 1' but that
                                                                           #would pass back all user info, including passwords.  So we move to step 6 

class EventSerializer(serializers.ModelSerializer):              # STEP_1: define the EventSerializer class to hold all serializers.  The code in the 
                                                                 # parenthesis means that this will be a model serializer (that sounds weird- I mean it will serialize a model)

    organizer = GamerSerializer()                               # STEP_3: make variable called organizer (must match up with the field we are building a nested serializer for, in this 
                                                                        #case the 'organizer' field from class Meta).  Call a new serializer called GamerSerializer.

    joined = serializers.BooleanField(required=False) 

    class Meta:                                                  
        model = Event                                                          # STEP_2A: make the Meta class to hold the model and model fields
        fields = ['id', 'organizer', 'game', 'date', 'time', 'description', 'attendees', 'joined']    # STEP_2B: We only want to pass back first/last name of organizer, which requires nested serializers, so we move to step 3      
        depth = 1                                                              # STEP_2C: Think of depth like JS expand.  Without it, a GET will only return the id number for the 'game' field.
                                                                                    # But depth one will return everything for the 'game' field (id, title, maker, num of players, skill level, game type, gamer) 
                                                                                    # The bigger the depth number, the more gets embedded.  If you set depth = 2, you'd get back gametype and gamer expanded.



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ NEXT STEP NOT IN THIS FILE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Now that you've made the EventView class, you have to add info from it into the urls.py file. You'll add:
                # router.register(r'events', EventView, 'event')

        # Then test your code with Postman to see if you can get events
                # Make sure your server is running (python3 manage.py runserver) a
                # In Postman, do a GET to http://localhost:8000/events and click 'send'
                # If the response in the body section (set it to JSON) is empty brackets, you don't have events in the database
                    # Add some by switching Postman to POST and setting the body to raw JSON.  URL stays the same as above.
                    # Build an event dictionary.  Here's a template to save time:
                      #  {
                      #      "gameId": 2,
                      #      "description": "This will be fun",
                      #      "date": "2021-12-03",
                      #      "time": "12:00:00"
                      #  }
                    # Click send and check for status 201 to confirm it was created.
                    # Try the GET again


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ EXTRA NOTES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # The try/except blocks do not affect whether or not a method will work.  Any method can fail or succeed without the block.  
    # The purpose of the try/except block is to give the client-side a more organized and specific error message.  Server side can predict 
    # what errors are likely, catch them, and specify an error message to display for the client side.  
    # Or, like in the create method try/except block on this file, you can build one that catches any error and displays the same message for them all