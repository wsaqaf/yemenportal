class Posts::TagsController < ApplicationController
  before_action :find_post, only: [:create, :index, :new, :destroy]

  def index
    render_tags_page
  end

  def destroy
    post_tag = PostTag.find(params.fetch(:id))
    post_tag.delete if post_tag.user == current_user
    render_tags_page
  end

  def new
    post_tag = PostTag.new(user: current_user, post: @post)
    render cell: "tags/form", model: post_tag, options: { tags: avaliable_tags }
  end

  def create
    post_tag = PostTagForm.new(PostTag.new)

    if post_tag.validate(post_tag_params)
      post_tag.save
      redirect_to post_tags_path(post_id: @post.id)
    else
      render cell: "tags/form", model: post_tag, options: { tags: avaliable_tags }
    end
  end

  private

  def render_tags_page
    render cell: "tags", model: @post.post_tags, options: { current_user: current_user, post: @post }
  end

  def avaliable_tags
    Tag.all.map(&:name) - @post.post_tags.map(&:name)
  end

  def find_post
    @post = Post.find(params.fetch(:post_id))
  end

  def post_tag_params
    @_post_tag_params ||= begin
      tag_params = params.require(:post_tag).permit(:description, :name)
      tag_params.merge(user: current_user, post: @post)
    end
  end
end
