import {
  Upload,
  Button,
  Typography,
  List,
  message,
  Progress,
  Modal,
  Image,
} from "antd";
import PropTypes from "prop-types";
import { RedoOutlined, InboxOutlined } from "@ant-design/icons";

import useApp from "./hook/useApp";

const { Dragger } = Upload;

ListItem.propTypes = {
  item: PropTypes.object.isRequired,
  onClickButton: PropTypes.func.isRequired,
  key: PropTypes.string.isRequired,
};

// ListItem
function ListItem({ item, onClickButton, key }) {
  return (
    <>
      <List.Item
        actions={[
          <Button key={key} onClick={() => onClickButton(item)}>
            Click me
          </Button>,
        ]}
      >
        <List.Item.Meta
          avatar={
            <Progress
              type="circle"
              status={item?.error == "None" ? null : "exception"}
              percent={
                item?.segmentation_path != "None"
                  ? item?.transformation_path != "None"
                    ? 100
                    : 50
                  : 50
              }
              size={50}
            />
          }
          title={`session - ${item.session_id}`}
        />
      </List.Item>
    </>
  );
}

// Main App
function App() {
  const { session, selectedItem, modelVisible, onSelectItem, onCloseModal } =
    useApp();

  return (
    <div
      style={{
        margin: "0px 20px 0px 20px",
      }}
    >
      <Typography.Title
        level={3}
        style={{
          textAlign: "center",
        }}
      >
        HoneyComb
      </Typography.Title>

      <div
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "baseline",
          gap: "16px",
        }}
      >
        <Dragger
          name="file"
          multiple={false}
          action="/api/predict"
          onChange={(info) => {
            const { status } = info.file;
            if (status !== "uploading") {
              console.log(info.file, info.fileList);
            }
            if (status === "done") {
              message.success(`${info.file.name} file uploaded successfully.`);
            } else if (status === "error") {
              message.error(`${info.file.name} file upload failed.`);
            }
          }}
        >
          <p className="ant-upload-drag-icon">
            {" "}
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">
            Click or drag file to this area to upload
          </p>
        </Dragger>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
        }}
      >
        <Button
          type="link"
          icon={<RedoOutlined />}
          onClick={() => window.location.reload(false)}
        >
          {" "}
          Refresh
        </Button>
      </div>

      <div
        style={{
          margin: "16px",
        }}
      >
        <List
          itemLayout="horizontal"
          dataSource={session ?? []}
          renderItem={(item, index) => (
            <ListItem
              key={index}
              item={item}
              onClickButton={(e) => onSelectItem(e)}
            />
          )}
        />
      </div>

      {/* Modal */}
      <Modal
        title={`Session ${selectedItem.title}`}
        centered
        open={modelVisible}
        onOk={onCloseModal}
        onCancel={onCloseModal}
        width={1000}
      >
        <Typography.Title level={4}>Original Image</Typography.Title>
        <Image
          style={{
            width: "50%",
          }}
          src={`/api/minio/${selectedItem.origin}?resp_type=data`}
        ></Image>
        <hr
          style={{
            marginTop: "20px",
          }}
        />
        <Typography.Title level={4}>Result</Typography.Title>
        {selectedItem.error != 'None' ? (
          <Typography.Text> - Error: {selectedItem.error}</Typography.Text>
        ) : (
          selectedItem.data.map((e, ind) => {
            if (e.path === "None") return null;

            return (
              <div
                key={ind}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  marginTop: "20px",
                }}
              >
                <Image
                  style={{
                    width: "15%",
                  }}
                  src={`/api/minio/${e?.path}?resp_type=data`}
                />
                <Typography.Text>
                  {" "}
                  - Is chemical structure?: {e?.isChem}
                </Typography.Text>
                <Typography.Text> - SMILES: {e?.smiles}</Typography.Text>
              </div>
            );
          })
        )}
      </Modal>
    </div>
  );
}

export default App;
