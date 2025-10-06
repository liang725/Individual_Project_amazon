#项目说明
  本项目按照文档要求，通过D3js实现数据可视化，使用snap数据集，基于Amazon商品共购数据，采用力导向热力图，节点即商品，边为共购，颜色映射分组；力导向布局使高相关商品自然聚簇、桥梁商品清晰可见，辅以拖拽-高亮-筛选等交互
#架构简要说明
amazon-copurchase-network-visualizer/
├─ data_files/
│  └─ amazon.json               // 前端数据源
├─ amazon_index.js          // 主可视化模块        
├─ index.html                  // 单页入口

├─ amazon-meta.txt / amazon0302.txt  // 原始数据
├─ txt_to_json.py              // 分布过滤和格式转换脚本
       
#整体预览（详细功能见说明文档）
<img width="2879" height="1715" alt="image" src="https://github.com/user-attachments/assets/1650736e-fa43-4210-9e4e-9e9d99dfbf92" />

