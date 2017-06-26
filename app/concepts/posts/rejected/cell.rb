class Posts::Rejected::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :user
  property :title, :link, :published_at, :property

  def table_body
    concept("posts/rejected/item/cell", collection: model, user: user)
  end
end
