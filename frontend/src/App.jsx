import { useState } from "react";
import { Upload, Button, Typography, List, Avatar, Progress} from "antd";
import { UploadOutlined } from "@ant-design/icons";

import useApp from "./hook/useApp";

function App() {
  const { session, loading } = useApp();

  const data = [
    {
      title: "Ant Design Title 1",
    },
    {
      title: "Ant Design Title 2",
    },
    {
      title: "Ant Design Title 3",
    },
    {
      title: "Ant Design Title 4",
    },
  ];

  return (
    <div>
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "baseline",
          gap: "16px",
        }}
      >
        <Typography.Title level={3}>Upload a picture</Typography.Title>
        <Upload>
          <Button icon={<UploadOutlined />}>Upload</Button>
        </Upload>
      </div>
      <div
        style={{
          margin: "16px",
        }}
      >
        <List
            itemLayout="horizontal"
            dataSource={data}
            renderItem={(item, index) => (
              <List.Item
                actions={[<Button>Click me</Button>]}
              >
                <List.Item.Meta
                  avatar={
                    <Progress type="circle" percent={20} size={50} />
                  }
                  title={<a href="https://ant.design">{item.title}</a>}
                  description="Ant Design, a design language for background applications, is refined by Ant UED Team"
                />
              </List.Item>
            )}
          />
      </div>

    </div>
  );
}

export default App;
