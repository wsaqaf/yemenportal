class Posts::CommentsController < ApplicationController
  def index
    render cell: "posts/comments", model: post
  end

  private

  def post
    ::Post.include_voted_by_user(current_user).find(params[:post_id])
  end
end
