import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import *
import re


#######################   MOVIE RECOMMENDER SYSTEM (MACHINE LEARNING) ###########################
#######################   BY      T.JOHN EMMANUEL URK18CS074   ###########################

class MovieRecommender:
    def __init__(self):
        ##Step 1: Reading the CSV File....The One I dwonloaded from IMDb
        self.df = pd.read_csv("movie_dataset.csv")
        ##Step 2: Select Features For Filtering of the data.
        self.features = ['keywords','cast','genres','director']
        self.cv = CountVectorizer()
        self.cosine_sim = None
        self.movies = self.df.title.values
        self.computeMatrix()
        
    ###### helper functions. Use them when needed #######
    def get_title_from_index(self, index):
    	return self.df[self.df.index == index]["title"].values[0]
    
    def get_index_from_title(self, title):
    	return self.df[self.df.title == title]["index"].values[0]
    
    ##Step 4: Here We Create a Data Frame of Combined Features.
    def combine_features(self, row):
    		return row['keywords'] +" "+row['cast']+" "+row["genres"]+" "+row["director"]
	
    def computeMatrix(self):
        ##Step 3: Here We Fill All the NaN values in the features.
        for feature in self.features:
        	self.df[feature] = self.df[feature].fillna('')
        
        self.df["combined_features"] = self.df.apply(self.combine_features,axis=1)
        
        ##Step 4: Create count matrix from this new combined column
        count_matrix = self.cv.fit_transform(self.df["combined_features"])

        ##Step 5: Compute the Cosine Similarity based on the count_matrix
        self.cosine_sim = cosine_similarity(count_matrix) 
        
    def recommend(self, movie_user_likes):
        #movie_user_likes = input("Enter a Movie which you like and I will give you my top 25 Recomendations:")
        
        ## Step 6: Get index of this movie from its title
        movie_index = self.get_index_from_title(movie_user_likes)
        similar_movies =  list(enumerate(self.cosine_sim[movie_index]))
        
        ## Step 7: Get a list of similar movies in descending order of similarity score
        sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)
        
        ## Step 8: Print titles of first 50 movies
        movie_string = " ------------------------------\n Recommended Movies \n ------------------------------"
        for element in sorted_similar_movies[1:25]:
        	movie_string = movie_string + "\n" + self.get_title_from_index(element[0])
        
        return movie_string
    
#mr = MovieRecommender()
#print(mr.recommend("The Smurfs"))
        
class AutocompleteEntry(Entry):
    def __init__(self, autocompleteList, *args, **kwargs):

        # Listbox length
        if 'listboxLength' in kwargs:
            self.listboxLength = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.listboxLength = 8

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)
                
            self.matchesFunction = matches

        
        Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.autocompleteList = autocompleteList
        
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)
        
        self.listboxUp = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if not self.listboxUp:
                    self.listbox = Listbox(width=self["width"], height=self.listboxLength)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.listboxUp = True
                
                self.listbox.delete(0, END)
                for w in words:
                    self.listbox.insert(END,w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False
        
    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(ACTIVE))
            self.listbox.destroy()
            self.listboxUp = False
            self.icursor(END)

    def moveUp(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != '0':                
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def moveDown(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
                
            if index != END:                        
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)
                
                self.listbox.see(index) # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index) 

    def comparison(self):
        return [ w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w) ]
    
class UI:
    def __init__(self):
        self.mr = MovieRecommender()
        self.autocompleteList = self.mr.movies
        self.root = Tk()
        self.outputLbl = Label(self.root, text = "")
        self.entry = None
      
    def matches(self, fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)

    def clicked(self):
        movieList = self.mr.recommend(self.entry.get())
        self.outputLbl.configure(text=movieList)
    
    def start(self):
        self.root.title("Movie Recommender System")
        self.root.geometry('500x700')
        lbl = Label(self.root, text="Enter your favorite movie : ")
        lbl.grid(row = 0, column = 0)
        self.entry = AutocompleteEntry(self.autocompleteList, self.root, listboxLength=6, width=32, matchesFunction=self.matches)
        self.entry.grid(row = 0, column=1)
        self.outputLbl.grid(row=2, column = 0 )
        btn = Button(self.root, text="Suggest movies!", command=self.clicked)
        btn.grid(row = 1, column = 0)
        self.root.mainloop()
        
ui = UI()
ui.start()
        

                
