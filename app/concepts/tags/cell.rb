class Tags::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :current_user, :post, :resolved
  property :title, :link, :published_at, :property

  def post_tags_list
    concept("tags/item/cell", collection: model, current_user: current_user)
  end

  def resolve_params
    { post_id: post.id, post_tag: { name: PostTag::RESOLVE_TAG } }
  end
end
