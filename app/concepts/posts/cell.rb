class Posts::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :categories, :state
  property :title, :link, :published_at, :property

  def posts_page
    concept("posts/#{state}/cell", model, categories: categories)
  end
end
