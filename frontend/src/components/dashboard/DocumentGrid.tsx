
import React from 'react';
import DocumentCard from '../../components/ui/DocumentCard';

interface Document {
  id: number;
  title: string;
  preview?: string;
  createdAt: Date;
  lastViewed?: Date;
  isProcessed?: boolean;
  subject?: string;
}

interface DocumentGridProps {
  documents: Document[];
  viewMode: 'grid' | 'list';
}

const DocumentGrid: React.FC<DocumentGridProps> = ({ documents, viewMode }) => {
  if (documents.length === 0) {
    return null;
  }

  return (
    <div className={`grid ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'} gap-6`}>
      {documents.map((doc) => (
        <DocumentCard
          key={doc.id}
          id={doc.id.toString()}
          title={doc.title}
          preview={doc.preview}
          createdAt={doc.createdAt}
          lastViewed={doc.lastViewed}
          isProcessed={doc.isProcessed}
          subject={doc.subject}
          className={viewMode === 'list' ? 'flex flex-col md:flex-row' : ''}
        />
      ))}
    </div>
  );
};

export default DocumentGrid;
