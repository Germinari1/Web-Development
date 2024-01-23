from django.shortcuts import render
from markdown import Markdown
from . import util
from django.http import HttpResponse
from random import choice
from django.contrib import messages

'''
TODO:
-  add funtion to delete pages
'''

#keep track of whatt is the index of the current "no title" (by creation or editing) page
#no_title_count = 0

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    """
    Given a request for a page, renders either the page requested (if it exists) or a 404 error page.
    """
    #get html content form .md file (or None if does not exist in storage)
    html = util.md_to_html(title)

    #display pages (requested one or error)
    if html == None:
        return render(request, "encyclopedia/error404.html", {
            "message": f"The page {title} does not exist."
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html
        })
def search(request):
    """
    Handles requests (via POST method) to perform searches on the encyclopedia. 
    """
    #handle request
    if request.method == 'POST':
        #get content of query
        query = request.POST['q']
        #list of recommendations
        recs = []

        #get html content (if query is identical to some entry`s title) or NULL (if this is not the case)
        html = util.md_to_html(query)
        if not html==None:
            #get exact page name to display
            for entry in util.list_entries():
                if query.lower() == entry.lower():
                    query = entry
            
            #return page
            return render(request, "encyclopedia/entry.html", {
            "title": query,
            "content": html
                })
        #display search resuls page if query is substring of some entry`s title
        else:
            for entry in util.list_entries():
                if query.lower() in entry.lower():
                    recs.append(entry)
            return render(request, "encyclopedia/search.html", {
                "recs": recs
            })
        
def new_page(request):
    """
    Helpes the creation of new pages for the website
    """
    global no_title_count
    #render new page 
    if request.method == 'GET':
        return render(request, "encyclopedia/new.html")
    #POST method - save page
    else:
        #get data submited from form
        title = request.POST['title']
        content = request.POST['content']

        #check if title already exists
        if title in util.list_entries():
            return render(request, "encyclopedia/error404.html", {
                "message":"This page already exists."
            })
        #check if title is empty
        #effecetively create new page
        else:
            #check if title is empty
            if len(title)==0:
                no_title_index = 0
                for name in util.list_entries():
                    if "Untitled_" in name:
                        no_title_index +=1
                title  = f"Untitled_{no_title_index}"
                #no_title_count +=1
            #save new page 
            util.save_entry(title, content)

            #convert content to html
            html = util.md_to_html(content)

            #render new page
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": html
            })
        
def edit_page(request):
    """
    Enables a user to edit the contents of a Wiki´s page
    """
    if request.method == 'POST':
        #get data from page
        title  = request.POST['entry_title']
        content = util.get_entry(title)
        #rende page with previous informaiton
        return render(request, "encyclopedia/edit.html", {
            "title" : title,
            "content" : content
        })
    
def save(request):
    """
    Saves edit made to a page
    """
    #check http header method
    if request.method == 'POST':
        #get page data and transform to the right format
        title  = request.POST['title']
        title_0 = request.POST['title_0']
        content = request.POST['content']
        #add generic name is title is edited to be an empty string
        if len(title)==0:
                no_title_index = 0
                for name in util.list_entries():
                    if "Untitled_" in name:
                        no_title_index +=1
                title  = f"Untitled_{no_title_index}"
        util.save_entry(title, content)
        if title!= title_0:
            util.delete_entry(title_0, content)
        html = util.md_to_html(title)

        #render edited and saved page
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html
        })
    
def random_page(request):
    """
    Takes the user to a random page within the Wiki application.
    """
    #select a random page entry
    title = choice(util.list_entries())

    #render page
    content = util.get_entry(title)
    util.save_entry(title, content)
    html = util.md_to_html(title)

    #render edited and saved page
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html
    })



