class PostsController < ApplicationController
  def show
    render cell: :show, model: post, layout: "iframe_layout"
  end

  private

  def post
    Post.find(params[:id])
  end
end
