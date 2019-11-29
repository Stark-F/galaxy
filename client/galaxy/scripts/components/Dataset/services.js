import axios from "axios";
import { timeAgo } from "utils/timeago";

/** Datasets request helper **/
export class Services {
    constructor(options = {}) {
        this.root = options.root;
    }

    async getDatasets(options = {}) {
        let params = "";
        if (options.sortBy) {
            if (options.sortBy === "update_time_ago") {
                options.sortBy = "update_time";
            }
            const sortPrefix = options.sortDesc ? "-dsc" : "-asc";
            params += `order=${options.sortBy}${sortPrefix}&`;
        }
        if (options.limit) {
            params += `limit=${options.limit}&`;
        }
        if (options.offset) {
            params += `offset=${options.offset}&`;
        }
        if (options.query) {
            params += `q=name-contains&qv=${options.query}&`;
        }
        const url = `${this.root}api/datasets?${params}`;
        try {
            const { data } = await axios.get(url);
            data.forEach( d => {
                d.update_time_ago = timeAgo(d.update_time);
            });
            return data;
        } catch (e) {
            this._errorMessage(e);
        }
    }

    async copyDataset(dataset_id, history_id) {
        const url = `${this.root}api/histories/${history_id}/contents`;
        try {
            const response = await axios.post(url, {
                type: "dataset",
                source: "hda",
                content: dataset_id
            });
            return response.data;
        } catch (e) {
            this._errorMessage(e);
        }
    }

    async setHistory(id) {
        const url = `${this.root}history/set_as_current?id=${id}`;
        try {
            const response = await axios.get(url);
            return response.data;
        } catch (e) {
            this._errorMessage(e);
        }
    }

    async updateTags(item_id, item_class, item_tags) {
        const url = `${this.root}api/tags`;
        try {
            const response = await axios.put(url, {
                item_id: item_id,
                item_class: item_class,
                item_tags: item_tags
            });
            return response.data;
        } catch (e) {
            this._errorMessage(e);
        }
    }

    _errorMessage(e) {
        let message = "Request failed.";
        if (e.response) {
            message = e.response.data.err_msg || `${e.response.statusText} (${e.response.status})`;
        }
        throw message;
    }
}
