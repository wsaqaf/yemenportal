class Tags::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :current_user, :post
  property :title, :link, :published_at, :property

  def post_tags_list
    concept("tags/item/cell", collection: model, current_user: current_user)
  end
end
