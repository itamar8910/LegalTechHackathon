# LegalTechHackathon Voice assistant
This is a voice assistant developed in the LegalTech Hackathon
In Tel Aviv, 23/2/18. 

The voice assitant provides 3 features (Hebrew only):
- Search info of a Judge
- Search for precedents
- Search for a Law's details

Overview:
1. An android app serves as the front end for speech recording, and sends the voice stream to the server through a tcp socket.
2. The server transforms that Speech signal to text with Google's Speech to Text.
3. When the server identifies a query, it retrieves the relevant data and displays it to the user in a web interface. 

Steps for searching for precedents:
1. Take the text that describes the event.
2. Transfer the words in the text to their base form
3. Use Facebook's Word2Vec implementation, FastText, and compute the average vectors for paragraphs (Average the words vectors).
4. Query a pre-processed KNN datastructure to find paragraphs with close vector representaions.
5. The final decision is weighed between the vector distance(retrieved from KNN) and sequence matching distance between paragraphs.


Authers:

- Itamar Shenhar  : itamar8910@gmail.com
- Gil Maman       : gil.maman.5@gmail.com
- Alon Melamud    : alonmem@gmail.com
- Dani Rubin: 	  : sbhruchi@gmail.com
- Tom Guter        : tomyguter@gmail.com




