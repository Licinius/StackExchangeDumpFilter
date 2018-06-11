import os
from lxml import etree
class StackExchangeFilter:
	'''
		Filter for StackExchange Dump
		Only filter : posts, votes, comments, postlinks, users and badges

	'''
	POSTS_FILEPATH = "Posts.xml"
	VOTES_FILEPATH = "Votes.xml"
	COMMENTS_FILEPATH = "Comments.xml"
	POSTLINKS_FILEPATH = "PostLinks.xml"
	USERS_FILEPATH = "Users.xml"
	BADGES_FILEPATH = "Badges.xml"

	def __init__(self,filepath):
		self.filepath = filepath + os.sep

	def posts(self,main_tag,extras_tags,minimum_answers=0):
		try:
			tree = etree.parse(self.filepath+__class__.POSTS_FILEPATH)
		except Exception:
			print("Invalid filepath : %s" %self.filepath+__class__.POSTS_FILEPATH)
			exit(-1)

		root_name = "posts"

		main_filter=""
		if(main_tag is not None):
			main_filter = 'contains(@Tags,"<%s>") and ' % main_tag

		extras_filters = ""
		first=True
		if(extras_tags is not None):
			extras_filters = " and ("
			for tag in extras_tags : 
				if(first!=True):
					extras_filters +=" or "
				else :
					first = False
				extras_filters += " contains(@Tags,'<%s>') " %tag
			extras_filters += ") "


		path = '//row[%s @AnswerCount>=%s %s ]' %(main_filter,minimum_answers,extras_filters)
		output_path = 'output/%s'% __class__.POSTS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree.xpath(path):
				output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
				possibleAnswers = row.xpath("following-sibling::*[@ParentId='%s']" %row.attrib['Id'])
				for answer in possibleAnswers:
					output.write(etree.tostring(answer,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def votes(self):
		try:
			tree_votes = etree.parse(self.filepath+__class__.VOTES_FILEPATH)
			tree_posts = etree.parse('output/'+__class__.POSTS_FILEPATH)
		except Exception:
			print("Error, vote")
			exit(-1)
		root_name = 'votes'
		output_path = 'output/%s'% __class__.VOTES_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_votes.xpath('//row'):				
				if (tree_posts.xpath('//row[@Id="%s"]' %row.attrib['PostId']) ):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write('</%s>' %root_name)


	def comments(self):
		try:
			tree_comments = etree.parse(self.filepath+__class__.COMMENTS_FILEPATH)
			tree_posts = etree.parse('output/'+__class__.POSTS_FILEPATH)
		except Exception:
			print("Error, comments")
			exit(-1)
		root_name = "comments"
		output_path = 'output/%s'% __class__.COMMENTS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_comments.xpath("//row"):
				if (tree_posts.xpath('//row[@Id="%s"]' %row.attrib['PostId'])):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def postLinks(self):
		try:
			tree_postLinks = etree.parse(self.filepath+__class__.POSTLINKS_FILEPATH)
			tree_posts = etree.parse('output/'+__class__.POSTS_FILEPATH)
		except Exception:
			print("Error, postlinks")
			exit(-1)
		root_name = "postlinks"
		output_path = 'output/%s'% __class__.POSTLINKS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_postLinks.findall("row"):
				if (tree_posts.xpath('//row[@Id="%s"]' %row.attrib['PostId']) 
					or tree_posts.xpath('//row[@Id="%s"]' %row.attrib['RelatedPostId'])) :
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def users(self):
		try:
			tree_users = etree.parse(self.filepath+__class__.USERS_FILEPATH)
			tree_posts = etree.parse('output/'+__class__.POSTS_FILEPATH)
			tree_comments = etree.parse('output/' + __class__.COMMENTS_FILEPATH)
		except Exception:
			print("Error, users")
			exit(-1)
		root_name = "users"
		output_path = 'output/%s'% __class__.USERS_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_users.xpath('//row'):
				# if the id of the row is present in at least one post
				userId = row.attrib['Id']
				if (tree_posts.xpath('//row[@OwnerUserId="%s" or @LastEditorUserId="%s"]' %(userId,userId))
					or tree_comments.xpath('//row[@UserId="%s"]' %userId)):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write("</%s>" %root_name)

	def badges(self):
		try:
			tree_badges = etree.parse(self.filepath+__class__.BADGES_FILEPATH)
			tree_users = etree.parse('output/'+__class__.USERS_FILEPATH)
		except Exception:
			print("Error, badges")
			exit(-1)
		root_name = 'votes'
		output_path = 'output/%s'% __class__.BADGES_FILEPATH
		with open(output_path,'w') as output:
			output.write("<%s>" %root_name)
			for row in tree_badges.xpath('//row'):				
				if (tree_users.xpath('//row[@Id="%s"]' %row.attrib['UserId']) ):
					output.write(etree.tostring(row,pretty_print=True).decode("utf-8"))
			output.write('</%s>' %root_name)