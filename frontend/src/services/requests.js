import api from './api';

export const getLeaveRequests = async (statusFilter = null) => {
  const params = statusFilter ? { status_filter: statusFilter } : {};
  const res = await api.get('/requests/leave', { params });
  return res.data;
};

export const createLeaveRequest = async (payload) => {
  const res = await api.post('/requests/leave', payload);
  return res.data;
};

export const getCorrectionRequests = async (statusFilter = null) => {
  const params = statusFilter ? { status_filter: statusFilter } : {};
  const res = await api.get('/requests/corrections', { params });
  return res.data;
};

export const createCorrectionRequest = async (payload) => {
  const res = await api.post('/requests/corrections', payload);
  return res.data;
};

export const reviewLeaveRequest = async (id, status, reviewNotes = null) => {
  const res = await api.patch(`/requests/leave/${id}/review`, {
    status,
    review_notes: reviewNotes,
  });
  return res.data;
};

export const reviewCorrectionRequest = async (id, status, reviewNotes = null) => {
  const res = await api.patch(`/requests/corrections/${id}/review`, {
    status,
    review_notes: reviewNotes,
  });
  return res.data;
};
