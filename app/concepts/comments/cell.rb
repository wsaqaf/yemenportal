class Comments::Cell < Application::Cell
  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source, :photo_url
end
