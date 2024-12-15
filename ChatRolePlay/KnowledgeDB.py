from langchain.vectorstores import DocArrayInMemorySearch
from langchain.indexes import VectorstoreIndexCreator
from langchain import embeddings


class KnowledgeDB:
    """
    本地知识库
    采用向量化存储和索引
    """

    def __init__(
        self,
        data_folder_path: str = None,
        data_file_path: str = None,
        data_type="txt",
        embedding_name="openai",
        top_k=4,
        debug=False
    ):
        self.data_folder_path = data_folder_path
        self.data_file_path = data_file_path
        self.data_type = data_type
        self.embedding_name = embedding_name
        self.top_k = top_k
        self.debug=debug
        self.init_db()

    def init_db(self):
        # 初始化数据加载装置
        base_loader = None
        if self.data_type == "txt":
            from langchain.document_loaders import TextLoader

            base_loader = TextLoader
        # TODO 支持更多格式的数据
        else:
            print(f"{self.data_type} is not supported yet!")
            return

        if self.data_folder_path:
            from langchain.document_loaders import DirectoryLoader

            self.loader = DirectoryLoader(
                path=self.data_folder_path,
                glob=f"**/*.{self.data_type}",
                loader_cls=base_loader,
            )
        elif self.data_file_path:
            self.loader = base_loader(file_path=self.data_file_path)
        else:
            print("Error: no data path given!")
            return

        # 加载数据
        self.docs = self.loader.load()

        # embedding工具
        if self.embedding_name == "openai":
            from langchain_openai import OpenAIEmbeddings
            self.embedding = OpenAIEmbeddings()
        # TODO 添加更多embedding工具
        else: 
            print(f"{self.embedding_name} is not supported yet, use OpenAIEmbeddings instead.")
            from langchain_openai import OpenAIEmbeddings
            self.embedding = OpenAIEmbeddings()

        # 构建向量化本地知识库
        self.db = DocArrayInMemorySearch.from_documents(
            documents=self.docs, embedding=self.embedding
        )

    def get_related_info(self, query: str) -> str:
        """从知识库中获取top_k个与query最相关的背景信息

        Args:
            query (str): 待查找的内容
        
        Returns:
            str: 相关信息
        """
        results = self.db.similarity_search(query, k=self.top_k)
        context = ""
        for doc in results:
            context += doc.page_content
            context += "\n"

        if self.debug:
            print(context)

        return context
        
