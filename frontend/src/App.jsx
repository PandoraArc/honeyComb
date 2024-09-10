import { Upload, Button, Typography, List, message, Progress, Modal, Image} from "antd";
import { RedoOutlined, InboxOutlined } from "@ant-design/icons";

import useApp from "./hook/useApp";

const { Dragger } = Upload;

function App() {
  const { session, loading, selectedItem, modelVisible, onSelectItem, onCloseModal} = useApp();

  return (
    <div
      style={{
        margin: "0px 20px 0px 20px"
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
          name='file'
          multiple={false}
          action="/api/predict"
          onChange={(info) => {
            const { status } = info.file;
            if (status !== 'uploading') {
              console.log(info.file, info.fileList);
            }
            if (status === 'done') {
              message.success(`${info.file.name} file uploaded successfully.`);
            } else if (status === 'error') {
              message.error(`${info.file.name} file upload failed.`);
            }
          }}
        >
          <p className="ant-upload-drag-icon"> <InboxOutlined /></p>
          <p className="ant-upload-text">Click or drag file to this area to upload</p>
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
            <List.Item actions={[
              <Button
                onClick={() => {onSelectItem(item)}}
              >Click me</Button>
            ]}>
              <List.Item.Meta
                avatar={
                  <Progress
                    type="circle"
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
              width: '50%'
            }}
            src={`/api/minio/${selectedItem.origin}?resp_type=data`}
          >
        </Image>
        <hr
          style={{
            marginTop: '20px'
          }}
        />
        <Typography.Title level={4}>Result</Typography.Title>
        {
          selectedItem.data.map((e, ind) => {
            
            if (e.path === 'None') return null;

            return(
              <div
                key={ind}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  marginTop: '20px'
                }}
              >
                <Image 
                  style={{
                    width: '15%'
                  }}
                  src={`/api/minio/${e?.path}?resp_type=data`}>
                </Image>
                <Typography.Text> - Is checmical sturture?: {e?.isChem}</Typography.Text>
                <Typography.Text> - SMILES: {e?.smiles}</Typography.Text>
              </div>
            )
          })
        }

      </Modal>


    </div>
  );
}

export default App;
