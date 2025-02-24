import React from 'react';
import { MapPin, Building, Calendar } from 'lucide-react';

const getStatusColor = (status) => {
  switch (status.toLowerCase()) {
    case 'applied':
      return 'bg-blue-100 text-blue-800';
    case 'interview':
      return 'bg-yellow-100 text-yellow-800';
    case 'offer':
      return 'bg-green-100 text-green-800';
    case 'rejected':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const ApplicationRow = ({ application }) => {
  const statusClass = getStatusColor(application.status);

  return (
    <div className="p-4 hover:bg-gray-50">
      <div className="flex justify-between items-start">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-medium text-gray-900">
              {application.position}
            </h3>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClass}`}>
              {application.status}
            </span>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center">
              <Building className="w-4 h-4 mr-1" />
              {application.company}
            </div>
            {application.location && (
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-1" />
                {application.location}
              </div>
            )}
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {application.date}
            </div>
          </div>

          {application.description && (
            <p className="text-sm text-gray-600 mt-2">
              {application.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApplicationRow;
