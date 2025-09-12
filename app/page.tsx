import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Leaf, Shield, MapPin, QrCode, Users, TrendingUp } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Leaf className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold text-foreground">HerbTrace</h1>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/collect" className="text-muted-foreground hover:text-foreground transition-colors">
              Collect
            </Link>
            <Link href="/verify" className="text-muted-foreground hover:text-foreground transition-colors">
              Verify
            </Link>
            <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors">
              Dashboard
            </Link>
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/verify">Scan QR</Link>
            </Button>
            <Button asChild>
              <Link href="/collect">Start Collecting</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <h2 className="text-4xl md:text-6xl font-bold text-foreground mb-6 text-balance">
            Authentic Ayurvedic Herbs,
            <span className="text-primary"> Verified Journey</span>
          </h2>
          <p className="text-xl text-muted-foreground mb-8 text-pretty max-w-2xl mx-auto">
            Track every Ayurvedic herb from farm to consumer with blockchain-powered transparency. Ensure authenticity,
            sustainability, and quality in every batch.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/collect" className="flex items-center gap-2">
                <Leaf className="h-5 w-5" />
                Start Collecting
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/verify" className="flex items-center gap-2">
                <QrCode className="h-5 w-5" />
                Verify Product
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12 text-foreground">Complete Traceability Solution</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="border-border/50 hover:border-primary/50 transition-colors">
              <CardHeader>
                <MapPin className="h-10 w-10 text-primary mb-2" />
                <CardTitle>GPS-Tagged Collection</CardTitle>
                <CardDescription>
                  Every herb batch is geo-tagged at the source with precise location data and harvest conditions.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Shield className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Blockchain Security</CardTitle>
                <CardDescription>
                  Immutable records ensure data integrity and prevent tampering throughout the supply chain.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 hover:border-primary/50 transition-colors">
              <CardHeader>
                <QrCode className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Consumer Verification</CardTitle>
                <CardDescription>
                  Scan QR codes to instantly access complete provenance information and quality certifications.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Users className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Multi-Stakeholder Platform</CardTitle>
                <CardDescription>
                  Connects farmers, processors, and consumers in a transparent ecosystem of trust.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 hover:border-primary/50 transition-colors">
              <CardHeader>
                <TrendingUp className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Sustainability Tracking</CardTitle>
                <CardDescription>
                  Monitor environmental impact and promote sustainable harvesting practices.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 hover:border-primary/50 transition-colors">
              <CardHeader>
                <Leaf className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Quality Assurance</CardTitle>
                <CardDescription>
                  Integrated quality testing and certification tracking for premium Ayurvedic products.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-3xl">
          <h3 className="text-3xl font-bold mb-6 text-foreground">Ready to Transform Your Supply Chain?</h3>
          <p className="text-lg text-muted-foreground mb-8">
            Join the growing network of verified Ayurvedic herb suppliers and consumers building trust through
            transparency.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/collect">Get Started</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/dashboard">View Dashboard</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card/30 py-8 px-4">
        <div className="container mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Leaf className="h-6 w-6 text-primary" />
            <span className="text-lg font-semibold text-foreground">HerbTrace</span>
          </div>
          <p className="text-muted-foreground">Blockchain-powered traceability for authentic Ayurvedic herbs</p>
        </div>
      </footer>
    </div>
  )
}
