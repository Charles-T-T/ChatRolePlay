from .BaseDB import BaseDB
import numpy as np
import random
import string
import os

from math import sqrt

class NaiveDB(BaseDB):
    def __init__(self):
        self.verbose = False
        self.init_db()

    def init_db(self):
        if(self.verbose):
            print("call init_db")
        self.vectors = []
        self.documents = []
        self.norms = []

    def save(self, file_path):
        print( "warning! directly save folder from dbtype NaiveDB has not been implemented yet, try use role_from_hf to load role instead" )

    def load(self, file_path):
        print( "warning! directly load folder from dbtype NaiveDB has not been implemented yet, try use role_from_hf to load role instead" )

    def recompute_norm( self ):
        # 补全这部分代码，self.norms 分别存储每个vector的l2 norm
        # 计算每个向量的L2范数
        self.norms = [sqrt(sum([x**2 for x in vec])) for vec in self.vectors]

    # NOTE 优化代码：利用numpy加速计算
    def search(self, query_vector, n_results):
        if self.verbose:
            print("call search")

        # 如果 norms 长度与 vectors 不一致，重新计算
        if len(self.norms) != len(self.vectors):
            self.recompute_norm()

        # 将 vectors 和 norms 转为 NumPy 数组以便批量计算
        vectors = np.array(self.vectors)
        norms = np.array(self.norms)

        # 计算查询向量的 L2 范数
        query_norm = np.linalg.norm(query_vector)
        if query_norm < 1e-20:  # 查询向量范数过小，直接返回空结果
            return []

        # 计算余弦相似度（dot product / norm product）
        query_vector = np.array(query_vector)
        dot_products = np.dot(vectors, query_vector)
        cosine_similarities = dot_products / (norms * query_norm)

        # 获取相似度和索引对，按相似度降序排序
        sorted_indices = np.argsort(cosine_similarities)[::-1]
        sorted_similarities = cosine_similarities[sorted_indices]

        # 去重并提取前 n_results，考虑相似度相同的情况
        unique_similarities = set()  # 用于存储已处理过的相似度（重复文本）
        top_documents = []

        for idx, similarity in zip(sorted_indices, sorted_similarities):
            similarity = round(similarity, 4)  # 截取一定小数位数，便于比较
            if similarity in unique_similarities:
                continue  # 如果相似度重复，跳过
            unique_similarities.add(similarity)  # 记录相似度

            document = self.documents[idx]
            top_documents.append(document)

            if len(top_documents) == n_results:
                break

        # 返回前 n_results 的文档和相似度
        return top_documents

    def init_from_docs(self, vectors, documents):
        if(self.verbose):
            print("call init_from_docs")
        self.vectors = vectors
        self.documents = documents 
        self.norms = []
