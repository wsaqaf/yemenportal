require "rails_helper"

describe HomePageController, type: :request do
  describe "#index" do
    let(:category) { create :category }

    context "without params" do
      let(:do_request) { get "/" }

      it "show a main page" do
        do_request

        expect(response).to have_http_status(:ok)
      end
    end

    context "with category params" do
      let(:do_request) { get "/home_page?category=#{category.name}" }
      let(:do_bed_request) { get "/home_page?magic_name" }

      it "show posts by category" do
        do_request

        expect(response).to have_http_status(:ok)
      end

      it "show a main page with incorrect params" do
        do_bed_request

        expect(response).to have_http_status(:ok)
      end
    end
  end
end
