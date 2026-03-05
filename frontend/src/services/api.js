import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8001"
});

export const uploadFile = (file) => {

  const formData = new FormData();
  formData.append("file", file);

  return API.post("/upload_file", formData);
};

export const getDocuments = () => API.get("/documents");

export const generateRules = (docId) =>
  API.post(`/generate_rules/${docId}`);

export const checkCompliance = (file) => {

  const formData = new FormData();
  formData.append("file", file);

  return API.post("/check_compliance", formData);
};