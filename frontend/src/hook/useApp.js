import { useEffect, useState } from "react";
import Axios from "axios";

function useApp() {

    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        Axios.get("http:localhost:12021/api/session").then((res) => {
            let data = [];
            res.data.forEach((item) => {
                console.log(item)
                // data.push({
                //     title: item[0],
                //     segmentation_path: item[1],
                //     classification_path: item[2],
                //     transformation_path: item[3],
                // });
            });
            setSession([]);
            setLoading(false);
        });
    }, []);

    return { session, loading };
}

export default useApp;