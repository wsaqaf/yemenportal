class Posts::PostItem::Cell < Application::Cell
  PREVIEW_SIZE = 180

  property :title, :link, :published_at, :description, :id, :category_ids

  def preview
    ActionView::Base.full_sanitizer.sanitize(description)[0..PREVIEW_SIZE].tr("\n", " ") + "..."
  end
end
