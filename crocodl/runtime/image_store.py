#    Copyright (C) 2020 crocoDL developers
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software
#   and associated documentation files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sqlite3
import json
import math
from crocodl.runtime.image_utils import ImageUtils

class ImageStore(object):

	def __init__(self,path="image_embeddings.db"):
		self.path = path
		db = sqlite3.connect(path)
		cursor = db.cursor()
		cursor.execute("create table if not exists embeddings(path string primary key,search string, thumbnail string)")
		cursor.execute("create table if not exists architecture(name string)")
		db.commit()
		self.uncommitted_count = 0

	def __len__(self):
		db = sqlite3.connect(self.path)
		cursor = db.cursor()
		cursor.execute("select count(*) from embeddings")
		return cursor.fetchone()[0]

	def clear(self):
		db = sqlite3.connect(self.path)
		cursor = db.cursor()
		cursor.execute("delete from embeddings")
		db.commit()

	def setArchitecture(self,architecture):
		db = sqlite3.connect(self.path)
		cursor = db.cursor()
		cursor.execute("delete from architecture")
		cursor.execute("insert into architecture values(?)", (architecture,))
		db.commit()

	def getArchitecture(self):
		db = sqlite3.connect(self.path)
		cursor = db.cursor()
		cursor.execute("select * from architecture")
		for row in cursor.fetchall():
			return row[0]
		return None

	def isEmpty(self):
		return len(self) == 0

	def open(self):
		self.db = sqlite3.connect(self.path)
		self.cursor = self.db.cursor()

	def addEmbedding(self,path,embedding,image):
		embedding_enc = json.dumps(embedding)
		self.cursor.execute("insert or replace into embeddings values(?,?,?)",(path,embedding_enc,ImageUtils.encodeThumbnail(image)))
		self.uncommitted_count += 1
		if self.uncommitted_count > 50:
			self.db.commit()
			self.uncommitted_count = 0

	def close(self):
		self.db.commit()
		self.cursor = None
		self.db = None

	def fetchAll(self,cursor):
		cnames = [c[0] for c in cursor.description]
		rows = []
		for row in cursor.fetchall():
			rows.append({v1: v2 for (v1, v2) in zip(cnames, row)})
		return rows

	def fetchImage(self,path):
		db = sqlite3.connect(self.path)
		cursor = db.cursor()
		cursor.execute("select thumbnail from embeddings where path = ?",(path,))
		for row in cursor.fetchall():
			return ImageUtils.decodeThumbnail(row[0])
		return None

	def distance(self,v1,v2):
		# compute cosine similarity
		dp = 0.0
		A = 0.0
		B = 0.0
		v = zip(v1,v2)
		for (e1,e2) in v:
			dp += e1*e2
			A += e1**2
			B += e2**2

		return dp / (math.sqrt(A) * math.sqrt(B))

	def similaritySearch(self,embedding,firstN=3,progress_cb=None):
		db = sqlite3.connect(self.path)
		cursor = db.cursor()
		distances = []
		counter = 0
		cursor.execute("select * from embeddings")
		for row in self.fetchAll(cursor):
			path = row["path"]
			candidate = json.loads(row["search"])
			d = self.distance(embedding,candidate)
			distances.append((path,d))
			distances = sorted(distances,key=lambda x:x[1],reverse=True)[:firstN]
			counter += 1
			if counter % 10 == 0:
				if progress_cb:
					progress_cb("Searched "+ str(counter) + " images")
		return list(map(lambda x:(x[0],x[1],self.fetchImage(x[0])),distances))