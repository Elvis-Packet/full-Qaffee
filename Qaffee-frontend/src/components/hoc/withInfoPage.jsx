import React, { Suspense } from 'react';
import Loader from '../ui/Loader';

const withInfoPage = (Component) => {
  return function InfoPageWrapper(props) {
    return (
      <Suspense fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader />
        </div>
      }>
        <Component {...props} />
      </Suspense>
    );
  };
};

export default withInfoPage; 