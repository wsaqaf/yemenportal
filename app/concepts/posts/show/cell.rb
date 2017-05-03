class Posts::Show::Cell < Application::Cell
  private

  property :title, :link, :published_at, :description, :id, :category_ids, :categories, :source, :photo_url, :state

  def field_name(field)
    t("source.fields.#{field}")
  end

  def category_names
    categories.map(&:name)
  end

  def path
    posts_path(state: "pending")
  end
end
