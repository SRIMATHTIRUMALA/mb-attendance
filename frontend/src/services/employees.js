import api from './api';

export const getEmployees = async () => {
  const res = await api.get('/employees');
  return res.data;
};

export const getEmployee = async (id) => {
  const res = await api.get(`/employees/${id}`);
  return res.data;
};

export const createEmployee = async (employeeData) => {
  const res = await api.post('/employees', employeeData);
  return res.data;
};

export const updateEmployee = async (id, updateData) => {
  const res = await api.patch(`/employees/${id}`, updateData);
  return res.data;
};
