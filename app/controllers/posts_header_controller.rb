class PostsHeaderController < ApplicationController
  def show
    allow_header_frame_render
    render cell: :show, model: post, layout: "post_header_layout"
  end

  private

  def post
    Post.find(params[:id])
  end

  def allow_header_frame_render
    response.headers["X-Frame-Options"] = "ALLOWALL"
  end
end
