class PostsHeaderController < ApplicationController
  def show
    render cell: :show, model: post, layout: "post_layout"
  end

  private

  def post
    Post.find(params[:id])
  end
end
