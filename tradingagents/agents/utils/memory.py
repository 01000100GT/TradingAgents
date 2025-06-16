# 本文件定义了金融情景记忆类，用于存储和检索过去的金融情景及其对应的投资建议。

import chromadb
from chromadb.config import Settings
from openai import OpenAI
import numpy as np
from ...dataflows.config import get_config


# 金融情景记忆类
class FinancialSituationMemory:
    # 初始化方法
    def __init__(self, name):
        # 获取配置
        config = get_config()
        model_config = config.get("model_config", {})
        
        # 使用配置初始化OpenAI客户端
        self.client = OpenAI(
            base_url=model_config.get("base_url"),
            api_key=model_config.get("api_key")
        )
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.create_collection(name=name)

    # 获取文本的嵌入向量
    def get_embedding(self, text):
        """Get OpenAI embedding for a text"""
        config = get_config()
        embedding_model = config.get("embedding_model", "text-embedding-ada-002")
        
        response = self.client.embeddings.create(
            model=embedding_model, input=text
        )
        return response.data[0].embedding

    # 添加金融情景及对应建议
    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    # 获取匹配的记忆
    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


# 当作为主程序运行时
if __name__ == "__main__":
    # 示例用法
    matcher = FinancialSituationMemory()

    # 示例数据
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # 添加示例情景和建议
    matcher.add_situations(example_data)

    # 示例查询
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
