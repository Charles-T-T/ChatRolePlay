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
        debug=False,
    ):
        self.data_folder_path = data_folder_path
        self.data_file_path = data_file_path
        self.data_type = data_type
        self.embedding_name = embedding_name
        self.top_k = top_k
        self.debug = debug
        self.init_db()

    def init_db(self):
        self.init_loader()
        self.init_docs()
        self.init_embedding()
        
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

    # TODO 支持更多格式的数据
    def init_loader(self):
        base_loader = None
        if self.data_type == "txt":
            from langchain.document_loaders import TextLoader

            base_loader = TextLoader
        elif self.data_type == "jsonl":
            # jsonl不能直接用于langchain的任何loader，采用其他方法
            self.loader = base_loader
            return
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

    def init_docs(self):
        # 无法用langchain的loader处理的情况
        if self.loader is None:
            if self.data_type == "jsonl":
                from langchain.schema import Document
                import json

                # 手动从.jsonl中构建langchain的Document
                self.docs = []
                with open(self.data_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line.strip())
                            self.docs.append(
                                Document(
                                    page_content=data["text"],
                                    # metadata={"luotuo_openai": data["luotuo_openai"]},
                                )
                            )
            else:
                print("Error: wrong in data loader.")
                return
        # 可以用langchain的loader处理的情况
        else:
            self.docs = self.loader.load()

    # TODO 添加更多embedding工具
    def init_embedding(self):
        if self.embedding_name == "openai":
            from langchain_openai import OpenAIEmbeddings

            self.embedding = OpenAIEmbeddings()
        else:
            print(
                f"{self.embedding_name} is not supported yet, use OpenAIEmbeddings instead."
            )
            from langchain_openai import OpenAIEmbeddings

            self.embedding = OpenAIEmbeddings()
