# Copyright 2020 Niall McCarroll
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sqlite3
import json
import math
from crocodl.utils.image_utils import ImageUtils

class ImageStore(object):

	def __init__(self,path="image_embeddings.db"):
		self.path = path
		db = sqlite3.connect(path)
		cursor = db.cursor()
		cursor.execute("create table if not exists embeddings(path string primary key,embedding string, thumbnail string)")
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
			candidate = json.loads(row["embedding"])
			d = self.distance(embedding,candidate)
			distances.append((path,d))
			distances = sorted(distances,key=lambda x:x[1],reverse=True)[:firstN]
			counter += 1
			if counter % 10 == 0:
				progress_cb("Searched "+ str(counter) + " images")
		return list(map(lambda x:(x[0],x[1],self.fetchImage(x[0])),distances))