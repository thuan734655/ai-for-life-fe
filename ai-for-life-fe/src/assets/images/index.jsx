// import Arrow from './icons/arrow.svg';
// import ArrowsExpand from './icons/arrows-expand.svg';

// Object chứa tất cả icon
const images = {
  //   Arrow,
  //   ArrowsExpand,
};

export const IconApp = ({ name, width = 24, height = 24, className = "" }) => {
  const IconComponent = images[name];

  if (!IconComponent) return null; // Tránh lỗi nếu tên icon không tồn tại

  return <IconComponent width={width} height={height} className={className} />;
};
