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

    # def search(self, query_vector , n_results):

    #     if(self.verbose):
    #         print("call search")

    #     if len(self.norms) != len(self.vectors):
    #         self.recompute_norm()

    #     # self.vectors 是list of list of float
    #     # self.norms 存储了每个vector的l2 norm
    #     # query_vector是list of float
    #     # 依次计算query_vector和vectors中每个vector的cosine similarity（注意vector的norm已经在self.norm中计算)
    #     # 并且给出最相近的至多n_results个结果
    #     # 把对应序号的documents 用list of string的形式return
    #     # TODO 补全这部分代码

    #     # 计算查询向量的范数
    #     query_norm = sqrt(sum([x**2 for x in query_vector]))

    #     # 计算余弦相似度
    #     similarities = []
    #     for vec, norm in zip(self.vectors, self.norms):
    #         dot_product = sum(q * v for q, v in zip(query_vector, vec))
    #         if query_norm < 1e-20:
    #             continue
    #         cosine_similarity = dot_product / (query_norm * norm)
    #         similarities.append(cosine_similarity)

    #     # 获取最相似的n_results个结果
    #     top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:n_results]
    #     top_documents = [self.documents[i] for i in top_indices]
    #     return top_documents

    # NOTE 优化代码：利用numpy加速计算
    # TODO 如果数据更大，考虑近似搜索算法（如 FAISS 或 Annoy）
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

        # 找到相似度最高的 n_results 个索引
        top_indices = np.argsort(cosine_similarities)[-n_results:][::-1]

        # 根据索引提取对应的文档
        top_documents = [self.documents[i] for i in top_indices]
        return top_documents

    def init_from_docs(self, vectors, documents):
        if(self.verbose):
            print("call init_from_docs")
        self.vectors = vectors
        self.documents = documents 
        self.norms = []
