import { useEffect, useState } from "react";
import Axios from "axios";

function useApp() {

    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedItem, setSelectedItem] = useState({
        title: '',
        data: []
    })
    const [modelVisible, setModalVisible] = useState(false)
    
    useEffect(() => {
        setLoading(true);
        Axios.get("/api/session").then((res) => {
            let data = [];
            res?.data?.data?.forEach((item) => {
                data.push({
                    session_id: item[0],
                    original_image_path: item[1],
                    segmentation_path: item[2]?.split(","),
                    classification_path: item[3]?.split(","),
                    classification_date: item[4]?.split(","),
                    transformation_path: item[5]?.split(","),
                    transformation_date: item[6]?.split(","),
                });
            });
            setSession(data);
            setLoading(false);
        });
    }, []);

    const onSelectItem = (item) => {
        let obj = {
            title: item.session_id,
            origin: item.original_image_path,
            data: []
        }
        for (let i = 0; i < item.segmentation_path.length; i++) {
           let file = {
            path: item.segmentation_path[i],
            isChem: item.classification_date[i],
            smiles: item.transformation_date[i]
           }
           obj.data.push(file)
        }
        console.log(obj)

        setSelectedItem(obj)
        setModalVisible(true)
    }

    const onCloseModal = () => {
        setModalVisible(false)
    }


    return { session, loading, selectedItem, modelVisible, onSelectItem, onCloseModal};
}

export default useApp;