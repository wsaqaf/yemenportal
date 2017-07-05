class Posts::ReaderController < ApplicationController
  layout "iframe_layout", only: [:show]
  before_action :find_post, only: [:update, :show]

  def show
    render cell: true, model: @post
  end

  private

  def find_post
    @post = Post.find(params.fetch(:post_id))
  end

  def back_url
    request.referer || root_path
  end
end
