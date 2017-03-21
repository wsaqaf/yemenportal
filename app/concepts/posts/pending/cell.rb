class Posts::Pending::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :categories
  property :title, :link, :published_at, :property

  def table_body
    concept("posts/pending/item/cell", collection: model)
  end
end
