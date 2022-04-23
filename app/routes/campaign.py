# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)
 
from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Campaign
from app.classes.forms import CampaignForm
from flask_login import login_required
import datetime as dt
 
# This is the route to list all posts
@app.route('/campaign/list')
# This means the user must be logged in to see this page
#@login_required
def campaignList():
    # This retrieves all of the 'posts' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'posts'.
    campaigns = Campaign.objects()
    # This renders (shows to the user) the posts.html template. it also sends the posts object
    # to the template as a variable named posts.  The template uses a for loop to display
    # each post.
    return render_template('campaigns.html',campaigns=campaigns)
 
# This route will get one specific post and any comments associated with that post.  
# The postID is a variable that must be passsed as a parameter to the function and
# can then be used in the query to retrieve that post from the database. This route
# is called when the user clicks a link on postlist.html template.
# The angle brackets (<>) indicate a variable.
@app.route('/campaign/<campaignID>')
# This route will only run if the user is logged in.
@login_required
def campaign(campaignID):
    # retrieve the post using the postID
    thisCampaign = Campaign.objects.get(id=campaignID)
 
    # Send the post object and the comments object to the 'post.html' template.
    return render_template('campaign.html',campaign=thisCampaign)
 
# This route will delete a specific post.  You can only delete the post if you are the author.
# <postID> is a variable sent to this route by the user who clicked on the trash can in the
# template 'post.html'.
# TODO add the ability for an administrator to delete posts.
@app.route('/campaign/delete/<CampaignID>')
# Only run this route if the user is logged in.
@login_required
def CampaignDelete(CampaignID):
    # retrieve the post to be deleted using the postID
    deleteCampaign = Campaign.objects.get(id=CampaignID)
    # check to see if the user that is making this request is the author of the post.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteCampaign.author:
        # delete the post using the delete() method from Mongoengine
        deleteCampaign.delete()
        # send a message to the user that the post was deleted.
        flash('The Campaign was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a campaign you don't own.")
    return redirect(url_for('campaignList'))
 
 
@app.route('/campaign/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def CampaignNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = CampaignForm()
 
    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object.
    if form.validate_on_submit():
 
        # This stores all the values that the user entered into the new post form.
        # Post() is a mongoengine method for creating a new post. 'newPost' is the variable
        # that stores the object that is the result of the Post() method.  
        newCampaign = Campaign(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            author = current_user.id,
            candidatename = form.candidatename.data,
            incumbentname = form.incumbentname.data,
            officelevel = form.officelevel.data,
            officelocation = form.officelocation.data,
            office = form.office.data,
            desiredbudget = form.desiredbudget.data,
            incumbentbudget = form.incumbentbudget.data,
            incumbentparty = form.incumbentparty.data,

   
            # This sets the modifydate to the current datetime.
            modifydate = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newCampaign.save()
        newCampaign.reload()
 
        # Once the new post is saved, this sends the user to that post using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that
        # routes code can be run. In this case the user just created a post so we want
        # to send them to that post. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('campaign',campaignID=newCampaign.id))
 
    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are
    # stored in the form object and are displayed on the form. take a look at postform.html to
    # see how that works.
    return render_template('campaignform.html',form=form)
 
 
# This route enables a user to edit a post.  This functions very similar to creating a new
# post except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original post. Read and understand the new post route
# before this one.
@app.route('/campaign/edit/<CampaignID>', methods=['GET', 'POST'])
@login_required
def CampaignEdit(CampaignID):
    editCampaign = Campaign.objects.get(id=CampaignID)
    # if the user that requested to edit this post is not the author then deny them and
    # send them back to the post. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editCampaign.author:
        flash("You can't edit a campaign you don't own.")
        return redirect(url_for('campaign',campaignID=CampaignID))
    # get the form object
    form = CampaignForm()
    # If the user has submitted the form then update the post.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editCampaign.update(
            candidatename = form.candidatename.data,
            incumbentname = form.incumbentname.data,
            officelevel = form.officelevel.data,
            officelocation = form.officelocation.data,
            office = form.office.data,
            desiredbudget = form.desiredbudget.data,
            incumbentbudget = form.incumbentbudget.data,
            incumbentparty = form.incumbentparty.data,
            modifydate = dt.datetime.utcnow
            
        )
        # After updating the document, send the user to the updated post using a redirect.
        return redirect(url_for('campaign',campaignID=CampaignID))
 
    # if the form has NOT been submitted then take the data from the editPost object
    # and place it in the form object so it will be displayed to the user on the template.
    
    form.candidatename.data = editCampaign.candidatename
    form.incumbentname.data = editCampaign.incumbentname
    form.officelevel.data = editCampaign.officelevel
    form.officelocation.data = editCampaign.officelocation
    form.office.data = editCampaign.office
    form.desiredbudget.data = editCampaign.desiredbudget
    form.incumbentbudget.data = editCampaign.incumbentbudget
    form.incumbentparty.data = editCampaign.incumbentparty
 
    # Send the user to the post form that is now filled out with the current information
    # from the form.
    return render_template('campaignform.html',form=form)