import React from 'react';
import { Helmet } from 'react-helmet-async';

const SEO = ({ 
  title, 
  description, 
  keywords,
  canonicalPath,
  ogType = 'website',
  ogImage,
  jsonLd,
  noindex = false
}) => {
  const siteUrl = 'https://jobrocket.co.za';
  const siteName = 'Job Rocket';
  const defaultImage = `${siteUrl}/favicon.png`;
  
  const fullTitle = title 
    ? `${title} | ${siteName}` 
    : `${siteName} | South Africa's Leading Job Board & Recruitment Platform`;
  
  const fullDescription = description || 
    'Find your dream job in South Africa. Browse thousands of jobs across all industries. Recruiters: post jobs, search CVs, and manage applications.';
  
  const canonicalUrl = canonicalPath ? `${siteUrl}${canonicalPath}` : siteUrl;
  const image = ogImage || defaultImage;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={fullDescription} />
      {keywords && <meta name="keywords" content={keywords} />}
      <link rel="canonical" href={canonicalUrl} />
      {noindex && <meta name="robots" content="noindex, nofollow" />}
      
      {/* Open Graph */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={fullDescription} />
      <meta property="og:image" content={image} />
      <meta property="og:site_name" content={siteName} />
      <meta property="og:locale" content="en_ZA" />
      
      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={fullDescription} />
      <meta name="twitter:image" content={image} />
      
      {/* JSON-LD Structured Data */}
      {jsonLd && (
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
      )}
    </Helmet>
  );
};

export default SEO;
