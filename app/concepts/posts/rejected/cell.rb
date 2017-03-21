class Posts::Rejected::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :categories
  property :title, :link, :published_at, :property

  def table_body
    concept("posts/rejected/item/cell", collection: model)
  end
end
