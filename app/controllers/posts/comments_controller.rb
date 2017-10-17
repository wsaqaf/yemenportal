class Posts::CommentsController < ApplicationController
  def index
    render cell: "posts/comments", model: post
  end

  private

  def post
    ::Post.find(params[:post_id])
  end
end
