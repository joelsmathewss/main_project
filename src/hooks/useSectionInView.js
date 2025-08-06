import { useEffect, useState } from "react";

const useSectionInView = (sectionId) => {
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const target = document.getElementById(sectionId);
    if (!target) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setInView(entry.isIntersecting);
      },
      {
        threshold: 0.1,
      }
    );

    observer.observe(target);

    return () => {
      if (target) observer.unobserve(target);
    };
  }, [sectionId]);

  return inView;
};

export default useSectionInView;
